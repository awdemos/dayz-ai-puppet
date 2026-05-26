class AIStateExporter
{
    static void ExportState(PlayerBase player)
    {
        if (!player)
            return;

        AIStateData state = new AIStateData();
        state.health = player.GetHealth("", "");
        state.blood = player.GetHealth("GlobalHealth", "Blood");
        state.energy = player.GetStatEnergy().Get();
        state.water = player.GetStatWater().Get();
        state.stamina = player.GetStatStamina().Get();
        state.position = player.GetPosition();
        state.direction = player.GetDirection();
        state.bleeding = player.IsBleeding();

        EntityAI handsEntity = player.GetHumanInventory().GetEntityInHands();
        if (handsEntity)
            state.handsItem = handsEntity.GetType();

        ExportInventory(player, state);

        string json;
        JsonFileLoader<AIStateData>.JsonSaveFile("$profile:DayZAIPuppet/state.json", state);

        JsonFileLoader<AIStateData>.JsonMakeData(json, state);
    }

    static void ExportInventory(PlayerBase player, AIStateData state)
    {
        if (!player)
            return;

        state.inventory.Clear();

        array<EntityAI> items = new array<EntityAI>();
        player.GetInventory().EnumerateInventory(InventoryTraversalType.PREORDER, items);

        for (int i = 0; i < items.Count(); i++)
        {
            EntityAI item = items.Get(i);
            if (item)
            {
                state.inventory.Insert(item.GetType());
            }
        }
    }
}

class AIStateData
{
    float health;
    float blood;
    float energy;
    float water;
    float stamina;
    vector position;
    vector direction;
    bool bleeding;
    string handsItem;
    ref array<string> inventory = new array<string>();
    float recentDamage;
    string timeOfDay;
    float temperature;
}
