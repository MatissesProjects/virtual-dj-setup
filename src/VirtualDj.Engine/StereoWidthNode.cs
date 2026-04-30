namespace VirtualDj.Engine
{
    public class StereoWidthNode
    {
        /// <summary>
        /// 1.0 = Original, 0.0 = Mono, > 1.0 = Extra Wide
        /// </summary>
        public float Width { get; set; } = 1.0f;

        public void Process(float[] left, float[] right, int count)
        {
            float[] mid = new float[count];
            float[] side = new float[count];

            MsMatrix.Encode(left, right, mid, side, count);

            for (int i = 0; i < count; i++)
            {
                side[i] *= Width;
            }

            MsMatrix.Decode(mid, side, left, right, count);
        }
    }
}
