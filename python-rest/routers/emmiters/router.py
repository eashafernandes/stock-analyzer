from applogger import logger
from interface.emmiter import analysis_emmiter
from fastapi import APIRouter, Body

router = APIRouter()

@router.post("/ma_rsi", tags=["Moving Average and  Relative Strength Index"])
async def ma_rsi_emmitter(data=Body(...)):
    calculator = analysis_emmiter({"logger": logger})
    dataobj = calculator.ma_rsi(data['data'])
    return dataobj

@router.post("/correlation", tags=["Correlation Analysis"])
async def correlation_emmiter(data=Body(...)):
    calculator = analysis_emmiter({"logger": logger})
    dataobj = calculator.correlation(data['data'])
    return dataobj
