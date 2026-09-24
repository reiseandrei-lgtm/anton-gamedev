using UnityEngine.Localization;
using UnityEngine.UIElements;

public class ScoreLabel
{
    // label.text = "Score" — старый вариант, в комментарии не считается
    readonly LocalizedString score = new LocalizedString("UI", "ui.score_fmt");

    public void Show(Label label, int value)
    {
        score.Arguments = new object[] { value };
        label.text = score.GetLocalizedString();
    }
}
