@echo off
echo Starting Medical Forms System...
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && node server.js --host 0.0.0.0 --port 3001"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm start -- --host 0.0.0.0 --port 3000"

echo.
echo Both servers are starting...
echo Backend: http://localhost:3001
echo Frontend: http://localhost:3000
echo.
echo Press any key to close this window (servers will continue running)
pause > nul