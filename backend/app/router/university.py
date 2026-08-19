from fastapi import APIRouter , Depends 

router = APIRouter(prefix="/university" , tags=['university']
                   )


@router.post("/")
async def AdmitToUniversity():
    pass