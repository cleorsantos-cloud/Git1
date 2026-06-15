@echo off
echo Instalando Claude Code...
echo.

REM Verifica se Node.js esta instalado
node --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo Node.js nao encontrado!
    echo Baixe e instale em: https://nodejs.org
    echo Depois de instalar o Node.js, rode este arquivo novamente.
    pause
    start https://nodejs.org
    exit /b 1
)

echo Node.js encontrado! Instalando Claude Code...
npm install -g @anthropic-ai/claude-code

echo.
echo Instalacao concluida!
echo Para usar, abra o CMD em qualquer pasta e digite: claude
echo.
pause
