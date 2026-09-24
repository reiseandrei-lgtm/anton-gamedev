using UnityEngine.UIElements;

public class Restart
{
    public void Show(Label label, Label score)
    {
        label.text = "Try again";
        score.text = "ui.score_fmt";
        var key = "ui.pause";
    }
}
