using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Logging;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.Extensions.Primitives;

namespace RouteServer.Controllers
{
	[ApiController]
	[Route("ConnectedService/[controller]")]
	public class UploadController : ControllerBase
	{
		private readonly IWebHostEnvironment _hostingEnvironment;

		public UploadController(IWebHostEnvironment hostingEnvironment)
		{
			this._hostingEnvironment = hostingEnvironment;
		}

		[HttpPost]
		public string Post(List<IFormFile> postedFiles)
		{
			string ret = "";

			// タイムゾーンを設定
			TimeZoneInfo jstZone = TimeZoneInfo.FindSystemTimeZoneById("Tokyo Standard Time");
			// 日本時間で現在の日付と時刻を取得
			DateTime jstDateTime = TimeZoneInfo.ConvertTimeFromUtc(DateTime.UtcNow, jstZone);

			string today = jstDateTime.ToString("yyyyMMdd");
			string uploadDirectoryPath = Path.Combine($"{Path.DirectorySeparatorChar}", "workspace", "uploaded", today);
			if (!Directory.Exists(uploadDirectoryPath))
			{
				Directory.CreateDirectory(uploadDirectoryPath);
			}

			List<string> uploadedFiles = new List<string>();
			foreach (IFormFile postedFile in postedFiles)
			{
				string time = jstDateTime.ToString("HHmmss");
				string fileName = time + "_" + Path.GetFileName(postedFile.FileName);
				string filePath = Path.Combine(uploadDirectoryPath, fileName);

				using (var fileStream = new FileStream(filePath, FileMode.Create))
				{
					postedFile.CopyTo(fileStream);
				}

				uploadedFiles.Add(filePath);
				ret += string.Format("<b>{0}</b> uploaded.<br />", fileName);
			}

			return ret;
		}
	}
}
