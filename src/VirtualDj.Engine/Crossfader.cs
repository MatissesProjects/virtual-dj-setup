using System;

namespace VirtualDj.Engine
{
    public enum CrossfaderCurve
    {
        Linear,
        EqualPower
    }

    public class Crossfader
    {
        public float Position { get; set; } = 0.5f; // 0.0 = Deck A, 1.0 = Deck B
        public CrossfaderCurve Curve { get; set; } = CrossfaderCurve.EqualPower;

        public void Process(float[] deckASamples, float[] deckBSamples, float[] outputSamples, int count)
        {
            float gainA, gainB;

            if (Curve == CrossfaderCurve.Linear)
            {
                gainA = 1.0f - Position;
                gainB = Position;
            }
            else // Equal Power
            {
                // Use sine/cosine for constant energy
                // gainA^2 + gainB^2 = 1
                gainA = (float)Math.Cos(Position * Math.PI * 0.5);
                gainB = (float)Math.Sin(Position * Math.PI * 0.5);
            }

            for (int i = 0; i < count; i++)
            {
                outputSamples[i] = (deckASamples[i] * gainA) + (deckBSamples[i] * gainB);
            }
        }
    }
}
