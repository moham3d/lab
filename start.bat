@echo off
REM Medical Forms System - Windows Start Script
REM Starts both backend and frontend servers

echo 🚀 Starting Medical Forms System
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

echo ✅ Node.js found
echo.

REM Check if pnpm is installed
pnpm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  pnpm not found, falling back to npm
    set PACKAGE_MANAGER=npm
) else (
    echo ✅ pnpm found
    set PACKAGE_MANAGER=pnpm
)

echo.

REM Start Backend
echo 📦 Starting Backend Server...
cd backend
if not exist node_modules (
    echo Installing backend dependencies...
    %PACKAGE_MANAGER% install
)
start "Medical Forms Backend" cmd /c "%PACKAGE_MANAGER% run dev"
cd ..
echo ✅ Backend started on port 3001
echo.

REM Wait a moment for backend to initialize
timeout /t 3 /nobreak >nul

REM Start Frontend
echo ⚛️ Starting Frontend Server...
cd frontend
if not exist node_modules (
    echo Installing frontend dependencies...
    %PACKAGE_MANAGER% install
)
start "Medical Forms Frontend" cmd /c "%PACKAGE_MANAGER% start"
cd ..
echo ✅ Frontend started on port 3000
echo.

echo 🎉 Both servers started successfully!
echo.
echo 🌐 Frontend: http://localhost:3000
echo 🔧 Backend: http://localhost:3001
echo.
echo Press any key to exit...
pause >nul