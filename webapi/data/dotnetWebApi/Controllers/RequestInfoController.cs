using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Logging;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System;
using Microsoft.Extensions.Primitives;
using System.Text;
using static System.Net.Mime.MediaTypeNames;
using System.Net;
using Microsoft.AspNetCore.Http.Extensions;
using System.Threading.Tasks;
using static System.Net.WebRequestMethods;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.WebUtilities;
using System.Net.Http.Headers;

namespace RouteServer.Controllers
{

    [Route("ConnectedService/[controller]")]
    [ApiController]
    public class RequestInfoController : ControllerBase
    {
        private readonly IWebHostEnvironment _hostingEnvironment;

        public RequestInfoController(IWebHostEnvironment hostingEnvironment)
        {
            this._hostingEnvironment = hostingEnvironment;
        }

        [HttpGet]
        public ContentResult Get()
        {
            StringBuilder ret = new StringBuilder();

            ret.Append("<html>");
            ret.Append("<head> <title>Request Info</title> </head>");
            ret.Append("<body>");

            ret.Append("<h2>Request Params</h2>");

            ret.Append("<table>");
            ret.Append("<tr><td> Method </td><td> " + Request.Method + " </td></tr>");
            ret.Append($"<tr><td> Display URI </td><td> {Request.GetDisplayUrl()} </td></tr>");
            ret.Append($"<tr><td> Encoded URI </td><td> {Request.GetEncodedUrl()} </td></tr>");
            ret.Append($"<tr><td> Protocol </td><td> " + Request.Protocol + " </td></tr>");

            foreach (var x in Request.Headers)
            {
                //ret.Append($"{x}:{Request.Headers.Values}\n");
                ret.Append($"<tr><td> header: {x.Key} </td><td> {x.Value} </td></tr>");
            }
            foreach (var x in Request.Query.Keys)
            {
                //ret.Append($"{x}:{Request.Query[x]}\n");
                ret.Append($"<tr><td> query: {x} </td><td> {Request.Query[x]} </td></tr>");
            }
            ret.Append("</table>");

            ret.Append("</body>");
            ret.Append("</html>");

            return new ContentResult
            {
                ContentType = "text/html",
                StatusCode = (int)HttpStatusCode.OK,
                Content = ret.ToString()
            };
        }

        [HttpPost]
        public async Task<ContentResult> Post()
        {
            DateTime dt = DateTime.Now;
            StringBuilder ret = new StringBuilder();

            ret.Append("<html>");
            ret.Append("<head> <title>Request Info</title> </head>");
            ret.Append("<body>");

            ret.Append("<h2>Request Params</h2>");

            ret.Append("<table>");
            ret.Append($"<tr><td> DateTime </td><td> {dt.ToString("yyyy/MM/dd HH:mm:ss")} </td></tr>");
            ret.Append(" <tr><td> Method </td><td> " + Request.Method + " </td></tr>");
            ret.Append($"<tr><td> Display URI </td><td> {Request.GetDisplayUrl()} </td></tr>");
            ret.Append($"<tr><td> Encoded URI </td><td> {Request.GetEncodedUrl()} </td></tr>");
            ret.Append($"<tr><td> Protocol </td><td> " + Request.Protocol + " </td></tr>");

            if (Request.HasFormContentType)
            {
                string dateStr = dt.ToString("yyyyMMdd");
                string timeStr = dt.ToString("yyyyMMdd_HHmmss");

                string contentRootPath = _hostingEnvironment.ContentRootPath;

                string directoryPath = contentRootPath + Path.DirectorySeparatorChar + "UploadedFiles" + Path.DirectorySeparatorChar + dateStr;
                if (!Directory.Exists(directoryPath))
                {
                    Directory.CreateDirectory(directoryPath);
                }


                //var mediaType = MediaTypeHeaderValue.Parse(Request.ContentType);

                //var boundary = mediaType.Parameters
                //    .Where(x => string.Equals(x.Name.ToString(), "boundary", StringComparison.OrdinalIgnoreCase))
                //    .FirstOrDefault()?.ToString();

                //var reader = new MultipartReader(boundary, Request.Body);


                //while (true)
                //{
                //    var section = await reader.ReadNextSectionAsync().ConfigureAwait(false);
                //    if (section == null)
                //        break;
                //}


                int i = 0;
                foreach (IFormFile x in Request.Form.Files)
                {
                    ret.Append($"<tr><td> File[{i}]:FileName </td><td> {x.FileName} </td></tr>");
                    foreach (var y in x.Headers)
                    {
                        ret.Append($"<tr><td> File[{i}]:{y.Key} </td><td> {y.Value} </td></tr>");
                    }

                    string filename = Path.GetFileName(x.FileName);

                    string filenameWithoutExt = Path.GetFileNameWithoutExtension(filename);
                    string filenameExt = Path.GetExtension(filename);
                    string filenameSave = filenameWithoutExt + "_" + timeStr + filenameExt;

                    string fileFullPath = directoryPath + Path.DirectorySeparatorChar + filenameSave;

                    using (var stream = new FileStream(fileFullPath, FileMode.Create))
                    {
                        await x.CopyToAsync(stream);
                    }

                    i++;
                }

                i = 0;
                foreach (var x in Request.Form)
                {
                    ret.Append($"<tr><td> Form[{i}]:header: {x.Key} </td><td> {x.Value} </td></tr>");
                    i++;
                }
            }

            foreach (var x in Request.Headers)
            {
                ret.Append($"<tr><td> header: {x.Key} </td><td> {x.Value} </td></tr>");
            }
            foreach (var x in Request.Query.Keys)
            {
                ret.Append($"<tr><td> query: {x} </td><td> {Request.Query[x]} </td></tr>");
            }
            ret.Append("</table>");

            ret.Append("</body>");
            ret.Append("</html>");

            return new ContentResult
            {
                ContentType = "text/html",
                StatusCode = (int)HttpStatusCode.OK,
                Content = ret.ToString()
            };

        }
  
    }
}
