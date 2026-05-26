class AIPlayerManager
{
    protected static ref AIPlayerManager s_Instance;
    protected PlayerBase m_AIPlayer;
    protected vector m_SpawnPosition = "6600 0 2600";
    protected ref Timer m_StateExportTimer;

    static AIPlayerManager GetInstance()
    {
        if (!s_Instance)
            s_Instance = new AIPlayerManager();
        return s_Instance;
    }

    void SpawnAIPlayer(vector position)
    {
        if (position != vector.Zero)
            m_SpawnPosition = position;

        if (m_AIPlayer)
        {
            GetGame().ObjectDelete(m_AIPlayer);
            m_AIPlayer = NULL;
        }

        m_AIPlayer = PlayerBase.Cast(GetGame().CreatePlayer(NULL, "SurvivorBase", m_SpawnPosition, 0, "NONE"));
        if (m_AIPlayer)
        {
            m_AIPlayer.GetStatEnergy().Set(100);
            m_AIPlayer.GetStatWater().Set(100);
            m_AIPlayer.SetHealth("", "", 100);
            OutfitPlayer(m_AIPlayer);
            Print("[DayZAIPuppet] AI player spawned at " + m_SpawnPosition);
        }
        else
        {
            Print("[DayZAIPuppet] ERROR: Failed to spawn AI player");
        }
    }

    void OutfitPlayer(PlayerBase player)
    {
        EntityAI item;

        item = player.GetInventory().CreateInInventory("TShirt_Blue");
        item = player.GetInventory().CreateInInventory("Jeans_Blue");
        item = player.GetInventory().CreateInInventory("AthleticShoes_Blue");

        EntityAI melee = player.GetHumanInventory().CreateInHands("KitchenKnife");
        if (!melee)
            player.GetInventory().CreateInInventory("KitchenKnife");

        item = player.GetInventory().CreateInInventory("Chemlight_White");
        item = player.GetInventory().CreateInInventory("Apple");
        item = player.GetInventory().CreateInInventory("SodaCan_Cola");

        Print("[DayZAIPuppet] AI player outfitted with starter gear");
    }

    PlayerBase GetAIPlayer()
    {
        return m_AIPlayer;
    }

    void StartStateExport(float intervalSec)
    {
        if (m_StateExportTimer)
            m_StateExportTimer.Run(intervalSec, this, "ExportState", NULL, true);

        if (!m_StateExportTimer)
        {
            m_StateExportTimer = new Timer(CALL_CATEGORY_SYSTEM);
            m_StateExportTimer.Run(intervalSec, this, "ExportState", NULL, true);
        }
        Print("[DayZAIPuppet] State export started, interval=" + intervalSec + "s");
    }

    void ExportState()
    {
        if (!m_AIPlayer)
            return;

        AIStateExporter.ExportState(m_AIPlayer);
    }

    void SetSpawnPosition(vector pos)
    {
        m_SpawnPosition = pos;
    }
}
