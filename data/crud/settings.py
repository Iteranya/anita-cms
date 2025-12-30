from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from data import models

def get_setting(db: Session, key: str) -> Optional[Dict[str, Any]]:
    setting = db.query(models.Setting).filter(models.Setting.key == key).first()
    return setting.value if setting else None

def get_all_settings(db: Session) -> Dict[str, Any]:
    settings = db.query(models.Setting).all()
    return {s.key: s.value for s in settings}

def save_setting(db: Session, key: str, value: Dict[str, Any]) -> models.Setting:
    db_setting = models.Setting(key=key, value=value)
    merged_setting = db.merge(db_setting)
    db.commit()
    return merged_setting