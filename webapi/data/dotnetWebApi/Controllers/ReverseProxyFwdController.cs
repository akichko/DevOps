using System;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;

namespace ReverseProxyExample.Controllers
{
    [ApiController]
    [Route("[controller]")]
    public class ReverseProxyFwdController : ControllerBase
    {
        private static readonly HttpClient _proxyHttpClient = new HttpClient(new HttpClientHandler
        {
            Proxy = new WebProxy("http://172.32.0.8:8080")
        });

        // GET ReverseProxyFwd
        [HttpGet("")]
        public async Task<IActionResult> Get() => await ProxyRequest();

        // GET ReverseProxyFwd/{path}
        [HttpGet("{**path}")]
        public async Task<IActionResult> ProxyRequest(string path = "")
        {
            // バックエンドサーバのURL
            var backendServerUrl = "https://www.google.com";

            try
            {
                // リクエストを作成
                var request = new HttpRequestMessage
                {
                    RequestUri = new Uri(backendServerUrl + "/" + path),
                    Method = new HttpMethod(Request.Method)
                };

                string[] allowedHeaders = { "header1", "Connection" };

                // リクエストヘッダをコピー
                foreach (var header in Request.Headers)
                {
                    if (allowedHeaders.Contains(header.Key))
                    {
                        request.Headers.TryAddWithoutValidation(header.Key, header.Value.ToArray());
                    }
                }

                // リクエストを送信
                var proxyResponse = await _proxyHttpClient.SendAsync(request);

                // レスポンスを返す
                var contentResult = new ContentResult
                {
                    Content = await proxyResponse.Content.ReadAsStringAsync(),
                    StatusCode = (int)proxyResponse.StatusCode,
                    ContentType = proxyResponse.Content.Headers.ContentType?.ToString()
                };

                return contentResult;
            }
            catch (Exception ex)
            {
                // エラーが発生した場合は、適切な処理を行ってください。
                return StatusCode(500, ex.Message);
            }
        }
    }
}
