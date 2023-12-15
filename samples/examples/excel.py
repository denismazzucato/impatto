def final_grade(
    HW1, HW2, HW3, HW4,
    QZ1, QZ2, QZ3, QZ4,
    EX1, EX2):
  HW_coeff = 0.2
  QZ_coeff = 0.3
  EX_coeff = 0.5
  HW_avg = HW_coeff * (HW1 + HW2 + HW3 + HW4) / 4
  QZ_avg = QZ_coeff * (QZ1 + QZ2 + QZ3 + QZ4) / 4
  EX_avg = EX_coeff * (EX1 + EX2) / 2
  avg = HW_avg + QZ_avg + EX_avg
  return avg