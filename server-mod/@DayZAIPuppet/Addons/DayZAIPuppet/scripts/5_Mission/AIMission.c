modded class MissionServer
{
    protected ref Timer m_AITimer;

    override void OnInit()
    {
        super.OnInit();

        Print("[DayZAIPuppet] MissionServer OnInit — initializing AI system");

        vector spawnPos = "6600 0 2600";

        string configPath = "$profile:DayZAIPuppet/config.json";
        AIConfigData config = new AIConfigData();
        if (FileExist(configPath))
        {
            JsonFileLoader<AIConfigData>.JsonLoadFile(configPath, config);
            if (config.spawnPosition != vector.Zero)
                spawnPos = config.spawnPosition;
            Print("[DayZAIPuppet] Loaded config from " + configPath);
        }
        else
        {
            config.spawnPosition = spawnPos;
            config.exportInterval = 2.0;
            config.initialGear = true;

            MakeDirectory("$profile:DayZAIPuppet");
            JsonFileLoader<AIConfigData>.JsonSaveFile(configPath, config);
            Print("[DayZAIPuppet] Created default config at " + configPath);
        }

        float delay = 10.0;
        GetGame().GetCallQueue(CALL_CATEGORY_SYSTEM).CallLater(SpawnAndStartAI, delay * 1000, false, spawnPos, config.exportInterval);
    }

    void SpawnAndStartAI(vector position, float exportInterval)
    {
        Print("[DayZAIPuppet] Spawning AI player...");
        AIPlayerManager.GetInstance().SpawnAIPlayer(position);
        AIPlayerManager.GetInstance().StartStateExport(exportInterval);
        Print("[DayZAIPuppet] AI system fully operational");
    }
}

class AIConfigData
{
    vector spawnPosition = "6600 0 2600";
    float exportInterval = 2.0;
    bool initialGear = true;
}
