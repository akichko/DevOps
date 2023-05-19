using System;
using System.Net.Http;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc;

namespace ReverseProxyExample.Controllers
{
    [ApiController]
    [Route("[controller]")]
	public class ReverseProxyController : ControllerBase
	{
		private static readonly HttpClient _httpClient = new HttpClient();

		// GET ReverseProxy
		[HttpGet("")]
		public async Task<IActionResult> Get() => await ProxyRequest();


		// GET ReverseProxy/{path}
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

				//request.Headers.TryAddWithoutValidation("Host", "www.google.com");

				// リクエストヘッダをコピー
				foreach (var header in Request.Headers)
				{
					if (allowedHeaders.Contains(header.Key))
					{
						request.Headers.TryAddWithoutValidation(header.Key, header.Value.ToArray());
					}
				}

				// リクエストを送信
				var response = await _httpClient.SendAsync(request);

				// レスポンスを作成
				var proxyResponse = new HttpResponseMessage(response.StatusCode);

				// レスポンスヘッダをコピー
				foreach (var header in response.Headers)
				{
					proxyResponse.Headers.TryAddWithoutValidation(header.Key, header.Value.ToArray());
				}

				// レスポンス本文をコピー
				proxyResponse.Content = response.Content;

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
