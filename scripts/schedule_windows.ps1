$Action = New-ScheduledTaskAction -Execute "python" -Argument "app.py"
$Trigger = New-ScheduledTaskTrigger -Daily -At 7:10am
$Settings = New-ScheduledTaskSettingsSet -Compatibility Win8
Register-ScheduledTask -Action $Action -Trigger $Trigger -TaskName "DailySignal" -Description "Run Money Autopilot daily" -Settings $Settings
