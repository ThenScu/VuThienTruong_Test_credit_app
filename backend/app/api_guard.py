# app/api_guard.py
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.model.users import User

# Giả lập lấy user đang đăng nhập (Tạm fix cứng ID = 1 là tài khoản Thèn Scu để test)
def get_current_user(db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == 1).first()
    if not user:
        raise HTTPException(status_code=401, detail="Vui lòng đăng nhập")
    return user

# Middleware kiểm tra quyền và trừ credit
def require_feature_and_credit(feature_code: str, credit_cost: int):
    def dependency(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        # 1. Check quyền (User có tính năng này trong DB không?)
        has_feature = any(uf.feature.code == feature_code for uf in current_user.unlocked_features)
        if not has_feature:
            raise HTTPException(
                status_code=403, 
                detail=f"Tài khoản chưa nâng cấp. Vui lòng mua gói có chứa tính năng {feature_code}!"
            )
        
        # 2. Check ví tiền (Ví còn đủ tiền trả cho lần xài này không?)
        if current_user.balance < credit_cost:
            raise HTTPException(
                status_code=402,
                detail=f"Số dư không đủ. Cần {credit_cost} credits, hiện có {current_user.balance} credits."
            )
            
        # 3. Trừ tiền (Tiêu hao credit)
        current_user.balance -= credit_cost
        db.commit()
        
        return current_user
    return dependency