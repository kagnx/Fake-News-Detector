# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main_ui.py'],
    pathex=[],
    binaries=[],
    datas=[('resources/a.ico', 'resources'), ('resources/a.png', 'resources'), ('artifacts', 'artifacts'), ('C:\\Users\\OguzKaan\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\xgboost\\lib\\xgboost.dll', 'xgboost\\lib'), ('C:\\Users\\OguzKaan\\AppData\\Local\\Programs\\Python\\Python313\\Lib\\site-packages\\lightgbm\\bin\\lib_lightgbm.dll', 'lightgbm\\bin')],
    hiddenimports=['sklearn', 'sklearn.calibration', 'sklearn.metrics', 'sklearn.model_selection', 'sklearn.feature_extraction', 'sklearn.feature_extraction.text', 'sklearn.linear_model', 'sklearn.svm', 'sklearn.ensemble._forest', 'sklearn.ensemble._gb', 'sklearn.ensemble._voting', 'sklearn.ensemble._stacking', 'sklearn.naive_bayes', 'sklearn.utils._typedefs', 'sklearn.neighbors._partition_nodes', 'xgboost', 'lightgbm', 'pydantic', 'fastapi', 'uvicorn', 'uvicorn.logging', 'uvicorn.loops', 'uvicorn.loops.auto', 'uvicorn.protocols', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'requests', 'urllib3', 'certifi', 'charset_normalizer', 'idna'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='YalanHaberTespit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources\\a.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='YalanHaberTespit',
)
