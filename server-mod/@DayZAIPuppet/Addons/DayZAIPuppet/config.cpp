class CfgPatches {
    class DayZAIPuppet {
        units[] = {};
        weapons[] = {};
        requiredVersion = 0.1;
        requiredAddons[] = {"DZ_Data", "DZ_Scripts"};
    };
};

class CfgMods {
    class DayZAIPuppet {
        dir = "@DayZAIPuppet";
        picture = "";
        action = "";
        hideName = 0;
        hidePicture = 0;
        name = "DayZ AI Puppet";
        author = "DayZ AI Puppet";
        version = "0.1.0";
        type = "mod";
        dependencies[] = {"Game", "World", "Mission"};
        class defs {
            class gameScriptModule {
                value = "";
                files[] = {"DayZAIPuppet/scripts/3_Game"};
            };
            class worldScriptModule {
                value = "";
                files[] = {"DayZAIPuppet/scripts/4_World"};
            };
            class missionScriptModule {
                value = "";
                files[] = {"DayZAIPuppet/scripts/5_Mission"};
            };
        };
    };
};
