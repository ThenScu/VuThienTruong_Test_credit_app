# app/controller/transactions.py
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.model.users import User
from app.model.packages import Package
from app.model.transactions import Transaction
from app.model.user_features import UserFeature
from app.dto.transactions import BuyPackageRequest

def buy_package(db: Session, request: BuyPackageRequest):
    """Xử lý giao dịch mua gói credits"""
    
    # 1. TÌM VÀ KHÓA DÒNG USER (Pessimistic Lock)
    # with_for_update() sẽ bắt các request khác phải chờ cho đến khi transaction này commit xong
    user = db.query(User).filter(User.id == request.user_id).with_for_update().first()
    if not user:
        raise HTTPException(status_code=404, detail="User không tồn tại")

    # 2. KIỂM TRA GÓI CREDITS
    package = db.query(Package).filter(Package.id == request.package_id).first()
    if not package:
        raise HTTPException(status_code=404, detail="Gói credits không tồn tại")

    # [Giả lập gọi qua cổng thanh toán VNPay/Stripe thành công ở đây]
    
    try:
        # 3. CỘNG CREDIT VÀO VÍ
        user.balance += package.credits_awarded
        user.tier = package.name.lower()
        
        # 4. UNLOCK TÍNH NĂNG (RBAC)
        # Lấy danh sách ID tính năng user đang có để tránh add trùng lặp
        current_feature_ids = {uf.feature_id for uf in user.unlocked_features}

        for feature in package.features:
            if feature.id not in current_feature_ids:
                new_user_feature = UserFeature(user_id=user.id, feature_id=feature.id)
                db.add(new_user_feature)

        # 5. LƯU LỊCH SỬ GIAO DỊCH
        new_transaction = Transaction(
            user_id=user.id,
            package_id=package.id,
            amount=package.price,
            credits_added=package.credits_awarded,
            status="SUCCESS"
        )
        db.add(new_transaction)

        # 6. LƯU TẤT CẢ VÀO DB
        db.commit()
        db.refresh(new_transaction)

        return new_transaction

    except Exception as e:
        # Nếu có bất kỳ lỗi gì xảy ra, Rollback lại toàn bộ để không bị mất tiền oan
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")