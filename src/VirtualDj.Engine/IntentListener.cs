using System.Net;
using System.Net.Sockets;
using System.Text;

namespace VirtualDj.Engine
{
    public class IntentListener : IDisposable
    {
        private readonly TcpListener _listener;
        private bool _isRunning;
        private readonly Thread _listenThread;

        public event Action<IntentType>? IntentReceived;

        public IntentListener(int port = 5555)
        {
            _listener = new TcpListener(IPAddress.Loopback, port);
            _listenThread = new Thread(ListenLoop) { IsBackground = true };
        }

        public void Start()
        {
            _isRunning = true;
            _listener.Start();
            _listenThread.Start();
            Console.WriteLine($"Intent Listener started on port 5555.");
        }

        private void ListenLoop()
        {
            try
            {
                while (_isRunning)
                {
                    using var client = _listener.AcceptTcpClient();
                    using var stream = client.GetStream();
                    byte[] buffer = new byte[4]; // 4 bytes for int
                    int bytesRead = stream.Read(buffer, 0, buffer.Length);
                    
                    if (bytesRead == 4)
                    {
                        int intentValue = BitConverter.ToInt32(buffer, 0);
                        if (Enum.IsDefined(typeof(IntentType), intentValue))
                        {
                            IntentReceived?.Invoke((IntentType)intentValue);
                        }
                    }
                }
            }
            catch (Exception ex) when (_isRunning)
            {
                Console.WriteLine($"Intent Listener Error: {ex.Message}");
            }
        }

        public void Stop()
        {
            _isRunning = false;
            _listener.Stop();
        }

        public void Dispose()
        {
            Stop();
        }
    }
}
