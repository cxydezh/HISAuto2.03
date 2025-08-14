from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.base import BaseModel

class PatientList(BaseModel):
    """患者列表"""
    __tablename__ = 'patient_list'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    patient_bed_num = Column(String(20), nullable=False)  # 床号
    patient_name = Column(String(100), nullable=False)  # 患者姓名
    patient_id = Column(String(50), nullable=False)  # 病历号
    patient_age = Column(Integer)  # 患者年龄
    patient_ward = Column(String(50), nullable=False)  # 病区
    patient_department_id = Column(String(50), ForeignKey('departments.code'), nullable=False)  # 科室
    attending_doctor_id = Column(Integer, ForeignKey('users.user_id'))  # 主治医生ID
    fellow_doctor_id = Column(Integer, ForeignKey('users.user_id'))  # 住院医生ID
    resistant_doctor_id = Column(Integer, ForeignKey('users.user_id'))  # 实习医生ID
    patient_diagnosis = Column(String(500))  # 患者诊断
    patient_care_rank = Column(String(50))  # 患者护理级别
    patient_fee = Column(String(50))  # 患者费用
    in_hospital_time = Column(DateTime)  # 入院时间
    out_hospital_time = Column(DateTime)  # 出院时间
    patient_note = Column(String(500))  # 患者的备注信息

    # 关系
    attending_doctor = relationship("User", foreign_keys=[attending_doctor_id])
    fellow_doctor = relationship("User", foreign_keys=[fellow_doctor_id])
    resistant_doctor = relationship("User", foreign_keys=[resistant_doctor_id])
    patient_department = relationship("Department", foreign_keys=[patient_department_id])   

    def discharge(self, discharge_time):
        """将患者标记为出院"""
        self.out_hospital_time = discharge_time
        return self

    def readmit(self):
        """将患者重新标记为入院"""
        self.out_hospital_time = None
        return self

    def get_folder_name(self):
        """获取患者文件夹名称"""
        return f"{self.patient_bed_num}_{self.patient_id}_{self.patient_name}"

    def get_archive_folder_name(self):
        """获取患者归档文件夹名称"""
        if self.out_hospital_time:
            return f"{self.out_hospital_time.strftime('%Y%m%d_%H%M%S')}"
        return None 
    def file_one(self,patient_id):
        """归档一个患者"""
        patient_list_backup = PatientListBackup(
            patient_bed_num=self.patient_bed_num,
            patient_name=self.patient_name,
            patient_id=self.patient_id,
            patient_age=self.patient_age,
            patient_ward=self.patient_ward,
            patient_department_id=self.patient_department_id,
            attending_doctor_id=self.attending_doctor_id,
            fellow_doctor_id=self.fellow_doctor_id,
            resistant_doctor_id=self.resistant_doctor_id,
            patient_diagnosis=self.patient_diagnosis,
            patient_care_rank=self.patient_care_rank,
            patient_fee=self.patient_fee,
            in_hospital_time=self.in_hospital_time,
            out_hospital_time=self.out_hospital_time,
            patient_note=self.patient_note)
        patient_list_backup.save()
        return patient_list_backup
class PatientListBackup(BaseModel):
    """患者列表备份"""
    __tablename__ = 'patient_list_backup'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, autoincrement=True)  # 主键ID
    patient_bed_num = Column(String(20), nullable=False)  # 床号
    patient_name = Column(String(100), nullable=False)  # 患者姓名
    patient_id = Column(String(50), nullable=False)  # 病历号
    patient_age = Column(Integer)  # 患者年龄
    patient_ward = Column(String(50), nullable=False)  # 病区
    patient_department_id = Column(String(50), ForeignKey('departments.code'), nullable=False)  # 科室
    attending_doctor_id = Column(Integer, ForeignKey('users.user_id'))  # 主治医生ID
    fellow_doctor_id = Column(Integer, ForeignKey('users.user_id'))  # 住院医生ID
    resistant_doctor_id = Column(Integer, ForeignKey('users.user_id'))  # 实习医生ID
    patient_diagnosis = Column(String(500))  # 患者诊断
    patient_care_rank = Column(String(50))  # 患者护理级别
    patient_fee = Column(String(50))  # 患者费用
    in_hospital_time = Column(DateTime)  # 入院时间
    out_hospital_time = Column(DateTime)  # 出院时间
    patient_note = Column(String(500))  # 患者的备注信息

    # 关系
    attending_doctor = relationship("User", foreign_keys=[attending_doctor_id])
    fellow_doctor = relationship("User", foreign_keys=[fellow_doctor_id])
    resistant_doctor = relationship("User", foreign_keys=[resistant_doctor_id])
    patient_department = relationship("Department", foreign_keys=[patient_department_id])   
