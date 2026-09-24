using Game.Analytics;

// Негативная фикстура: строковое имя события, Send в обход AnalyticsEvents, PII-ключ, Consent не выставляется,
// run_ended и spark_collected не вызываются.
public class RunTelemetry
{
    public void OnBoot(int sessionIndex, string build) => AnalyticsEvents.SessionStarted(sessionIndex, build);

    public void OnJump(int index, float charge, float sinceStart, bool landed) =>
        AnalyticsEvents.JumpPerformed(index, charge, sinceStart, landed);

    public void OnRunStart(int runIndex, float sinceDeath)
    {
        AnalyticsLog.Send("run_started", ("run_index", runIndex), ("player_email", "a@b.c"));
    }
}
