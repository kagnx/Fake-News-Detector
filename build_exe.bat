@echo off
echo ============================================
echo   YALAN HABER TESPIT SISTEMI - EXE OLUSTUR
echo ============================================
echo.

cd /d "%~dp0"

echo [1/3] Temizlik yapiliyor...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

echo [2/3] EXE olusturuluyor...
pyinstaller ^
    --noconfirm ^
    --onedir ^
    --windowed ^
    --name "YalanHaberTespit" ^
    --icon "resources/a.ico" ^
    --add-data "resources/a.ico;resources" ^
    --add-data "resources/a.png;resources" ^
    --add-data "artifacts;artifacts" ^
    --add-data "C:\Users\OguzKaan\AppData\Local\Programs\Python\Python313\Lib\site-packages\xgboost\lib\xgboost.dll;xgboost\lib" ^
    --add-data "C:\Users\OguzKaan\AppData\Local\Programs\Python\Python313\Lib\site-packages\lightgbm\bin\lib_lightgbm.dll;lightgbm\bin" ^
    --hidden-import "sklearn" ^
    --hidden-import "sklearn.calibration" ^
    --hidden-import "sklearn.metrics" ^
    --hidden-import "sklearn.model_selection" ^
    --hidden-import "sklearn.feature_extraction" ^
    --hidden-import "sklearn.feature_extraction.text" ^
    --hidden-import "sklearn.linear_model" ^
    --hidden-import "sklearn.svm" ^
    --hidden-import "sklearn.ensemble._forest" ^
    --hidden-import "sklearn.ensemble._gb" ^
    --hidden-import "sklearn.ensemble._voting" ^
    --hidden-import "sklearn.ensemble._stacking" ^
    --hidden-import "sklearn.naive_bayes" ^
    --hidden-import "sklearn.utils._typedefs" ^
    --hidden-import "sklearn.neighbors._partition_nodes" ^
    --hidden-import "xgboost" ^
    --hidden-import "lightgbm" ^
    --hidden-import "pydantic" ^
    --hidden-import "fastapi" ^
    --hidden-import "uvicorn" ^
    --hidden-import "uvicorn.logging" ^
    --hidden-import "uvicorn.loops" ^
    --hidden-import "uvicorn.loops.auto" ^
    --hidden-import "uvicorn.protocols" ^
    --hidden-import "uvicorn.protocols.http" ^
    --hidden-import "uvicorn.protocols.http.auto" ^
    --hidden-import "uvicorn.protocols.websockets" ^
    --hidden-import "uvicorn.protocols.websockets.auto" ^
    --hidden-import "uvicorn.lifespan" ^
    --hidden-import "uvicorn.lifespan.on" ^
    --hidden-import "requests" ^
    --hidden-import "urllib3" ^
    --hidden-import "certifi" ^
    --hidden-import "charset_normalizer" ^
    --hidden-import "idna" ^
    main_ui.py

echo.
echo [3/3] Tamamlandi!
echo.
echo EXE dosyasi: dist\YalanHaberTespit\YalanHaberTespit.exe
echo.
pause
