using Game.Analytics;

// Позитивная фикстура check_analytics_calls.py: все события events.md вызываются через AnalyticsEvents,
// согласие выставляется из настроек.
public class RunTelemetry
{
    public void OnBoot(bool consent, int sessionIndex, string build)
    {
        AnalyticsLog.Consent = consent;
        AnalyticsEvents.SessionStarted(sessionIndex, build);
    }

    public void OnJump(int index, float charge, float sinceStart, bool landed) =>
        AnalyticsEvents.JumpPerformed(index, charge, sinceStart, landed);

    public void OnRunStart(int runIndex, float sinceDeath) => AnalyticsEvents.RunStarted(runIndex, sinceDeath);

    public void OnRunEnd(int runIndex, int score, int jumps) => AnalyticsEvents.RunEnded(runIndex, score, jumps);

    public void OnSpark(int value, float distance) => AnalyticsEvents.SparkCollected(value, distance);
}
