﻿using Kyoo.Models;
using Microsoft.Extensions.Configuration;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Threading.Tasks;

namespace Kyoo.Controllers.ThumbnailsManager
{
    public class ThumbnailsManager : IThumbnailsManager
    {
        private readonly IConfiguration config;

        public ThumbnailsManager(IConfiguration configuration)
        {
            config = configuration;
        }

        public async Task<Show> Validate(Show show)
        {
            if (show == null || show.Path == null)
                return null;
            string localThumb = Path.Combine(show.Path, "poster.jpg");
            string localLogo = Path.Combine(show.Path, "logo.png");
            string localBackdrop = Path.Combine(show.Path, "backdrop.jpg");


            if (show.ImgPrimary != null && !File.Exists(localThumb))
            {
                try
                {
                    using WebClient client = new WebClient();
                    await client.DownloadFileTaskAsync(new Uri(show.ImgPrimary), localThumb);
                }
                catch (WebException)
                {
                    Console.Error.WriteLine("Couldn't download an image.");
                }
            }

            if (show.ImgLogo != null && !File.Exists(localLogo))
            {
                try
                {
                    using WebClient client = new WebClient();
                    await client.DownloadFileTaskAsync(new Uri(show.ImgLogo), localLogo);
                }
                catch (WebException)
                {
                    Console.Error.WriteLine("Couldn't download an image.");
                }
            }

            if (show.ImgBackdrop != null && !File.Exists(localBackdrop))
            {
                try
                {
                    using WebClient client = new WebClient();
                    await client.DownloadFileTaskAsync(new Uri(show.ImgBackdrop), localBackdrop);
                }
                catch (WebException)
                {
                    Console.Error.WriteLine("Couldn't download an image.");
                }
            }

            return show;
        }

        public async Task<IEnumerable<People>> Validate(IEnumerable<People> people)
        {
            if (people == null)
                return null;
            foreach (People peop in people)
            {
                string root = config.GetValue<string>("peoplePath");
                Directory.CreateDirectory(root);

                string localThumb = root + "/" + peop.Slug + ".jpg";
                if (peop.ImgPrimary == null || File.Exists(localThumb))
                    continue;
                try
                {
                    using WebClient client = new WebClient();
                    await client.DownloadFileTaskAsync(new Uri(peop.ImgPrimary), localThumb);
                }
                catch (WebException)
                {
                    Console.Error.WriteLine("Couldn't download an image.");
                }
            }

            return people;
        }

        public async Task<Episode> Validate(Episode episode)
        {
            if (episode == null || episode.Path == null)
                return null;
            string localThumb = Path.ChangeExtension(episode.Path, "jpg");
            if (episode.ImgPrimary == null || File.Exists(localThumb))
                return episode;
            try
            {
                using WebClient client = new WebClient();
                await client.DownloadFileTaskAsync(new Uri(episode.ImgPrimary), localThumb);
            }
            catch (WebException)
            {
                Console.Error.WriteLine("Couldn't download an image.");
            }

            return episode;
        }
    }
}