namespace VirtualDj.Engine
{
    public static class MsMatrix
    {
        public static void Encode(float[] left, float[] right, float[] mid, float[] side, int count)
        {
            for (int i = 0; i < count; i++)
            {
                // Mid = (L + R) / 2
                // Side = (L - R) / 2
                mid[i] = (left[i] + right[i]) * 0.5f;
                side[i] = (left[i] - right[i]) * 0.5f;
            }
        }

        public static void Decode(float[] mid, float[] side, float[] left, float[] right, int count)
        {
            for (int i = 0; i < count; i++)
            {
                // L = Mid + Side
                // R = Mid - Side
                left[i] = mid[i] + side[i];
                right[i] = mid[i] - side[i];
            }
        }
    }
}
