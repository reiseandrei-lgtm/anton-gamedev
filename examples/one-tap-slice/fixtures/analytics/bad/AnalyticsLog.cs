// Бэкенд без проверки согласия (AN4)
namespace Game.Analytics
{
    public static class AnalyticsLog
    {
        public static bool Consent { get; set; }
        public static void Send(string eventName, params (string key, object value)[] parameters) { }
    }
}
