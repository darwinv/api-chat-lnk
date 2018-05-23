"""Archivo para identificar que campos fueron duplicados en otras tablas"""
"""Tomar en cuenta al momento de actualizar modelos relacionales"""
class QueryPlansAcquired():
    plan_name = models.CharField()

class Message():
    code = models.CharField()
