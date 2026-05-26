class AIPlayerComponent
{
    protected PlayerBase m_Player;
    protected float m_LastHealth;
    protected float m_TickAccumulator;
    protected float m_TickInterval = 0.5;

    void AIPlayerComponent(PlayerBase player)
    {
        m_Player = player;
        m_LastHealth = player.GetHealth("", "");
    }

    void OnTick(float dt)
    {
        m_TickAccumulator += dt;
        if (m_TickAccumulator < m_TickInterval)
            return;
        m_TickAccumulator = 0;

        float currentHealth = m_Player.GetHealth("", "");
        float damageDelta = m_LastHealth - currentHealth;
        m_LastHealth = currentHealth;

        if (damageDelta > 5.0)
        {
            Print("[DayZAIPuppet] Significant damage detected: " + damageDelta);
        }
    }

    float GetHealth()
    {
        if (!m_Player) return 0;
        return m_Player.GetHealth("", "");
    }

    float GetBlood()
    {
        if (!m_Player) return 0;
        return m_Player.GetHealth("GlobalHealth", "Blood");
    }

    float GetEnergy()
    {
        if (!m_Player) return 0;
        return m_Player.GetStatEnergy().Get();
    }

    float GetWater()
    {
        if (!m_Player) return 0;
        return m_Player.GetStatWater().Get();
    }

    float GetStamina()
    {
        if (!m_Player) return 0;
        return m_Player.GetStatStamina().Get();
    }

    vector GetPosition()
    {
        if (!m_Player) return "0 0 0";
        return m_Player.GetPosition();
    }

    vector GetDirection()
    {
        if (!m_Player) return "1 0 0";
        return m_Player.GetDirection();
    }

    string GetHandsItem()
    {
        if (!m_Player) return "";
        EntityAI hands = m_Player.GetHumanInventory().GetEntityInHands();
        if (hands)
            return hands.GetType();
        return "";
    }

    bool IsBleeding()
    {
        if (!m_Player) return false;
        return m_Player.IsBleeding();
    }

    float GetRecentDamage()
    {
        float currentHealth = m_Player.GetHealth("", "");
        float damage = m_LastHealth - currentHealth;
        return damage;
    }
}
