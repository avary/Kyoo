// Kyoo - A portable and vast media library solution.
// Copyright (c) Kyoo.
//
// See AUTHORS.md and LICENSE file in the project root for full license information.
//
// Kyoo is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// any later version.
//
// Kyoo is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Kyoo. If not, see <https://www.gnu.org/licenses/>.

using System;
using System.Linq;
using EntityFrameworkCore.Projectables;
using Kyoo.Abstractions.Models.Attributes;

namespace Kyoo.Abstractions.Models
{
	/// <summary>
	/// Has the user started watching, is it planned?
	/// </summary>
	public enum WatchStatus
	{
		/// <summary>
		/// The user has already watched this.
		/// </summary>
		Completed,

		/// <summary>
		/// The user started watching this but has not finished.
		/// </summary>
		Watching,

		/// <summary>
		/// The user does not plan to continue watching.
		/// </summary>
		Droped,

		/// <summary>
		/// The user has not started watching this but plans to.
		/// </summary>
		Planned,
	}

	/// <summary>
	/// Metadata of what an user as started/planned to watch.
	/// </summary>
	public class MovieWatchInfo : IAddedDate
	{
		/// <summary>
		/// The ID of the user that started watching this episode.
		/// </summary>
		[SerializeIgnore] public Guid UserId { get; set; }

		/// <summary>
		/// The user that started watching this episode.
		/// </summary>
		[SerializeIgnore] public User User { get; set; }

		/// <summary>
		/// The ID of the movie started.
		/// </summary>
		[SerializeIgnore] public Guid MovieId { get; set; }

		/// <summary>
		/// The <see cref="Movie"/> started.
		/// </summary>
		[SerializeIgnore] public Movie Movie { get; set; }

		/// <inheritdoc/>
		public DateTime AddedDate { get; set; }

		/// <summary>
		/// Has the user started watching, is it planned?
		/// </summary>
		public WatchStatus Status { get; set; }

		/// <summary>
		/// Where the player has stopped watching the movie (in seconds).
		/// </summary>
		/// <remarks>
		/// Null if the status is not Watching.
		/// </remarks>
		public int? WatchedTime { get; set; }
	}

	public class EpisodeWatchInfo : IAddedDate
	{
		/// <summary>
		/// The ID of the user that started watching this episode.
		/// </summary>
		[SerializeIgnore] public Guid UserId { get; set; }

		/// <summary>
		/// The user that started watching this episode.
		/// </summary>
		[SerializeIgnore] public User User { get; set; }

		/// <summary>
		/// The ID of the episode started.
		/// </summary>
		[SerializeIgnore] public Guid? EpisodeId { get; set; }

		/// <summary>
		/// The <see cref="Episode"/> started.
		/// </summary>
		[SerializeIgnore] public Episode Episode { get; set; }

		/// <inheritdoc/>
		public DateTime AddedDate { get; set; }

		/// <summary>
		/// Has the user started watching, is it planned?
		/// </summary>
		public WatchStatus Status { get; set; }

		/// <summary>
		/// Where the player has stopped watching the episode (in seconds).
		/// </summary>
		/// <remarks>
		/// Null if the status is not Watching.
		/// </remarks>
		public int? WatchedTime { get; set; }
	}

	public class ShowWatchInfo : IAddedDate
	{
		/// <summary>
		/// The ID of the user that started watching this episode.
		/// </summary>
		[SerializeIgnore] public Guid UserId { get; set; }

		/// <summary>
		/// The user that started watching this episode.
		/// </summary>
		[SerializeIgnore] public User User { get; set; }

		/// <summary>
		/// The ID of the show started.
		/// </summary>
		[SerializeIgnore] public Guid ShowId { get; set; }

		/// <summary>
		/// The <see cref="Show"/> started.
		/// </summary>
		[SerializeIgnore] public Show Show { get; set; }

		/// <inheritdoc/>
		public DateTime AddedDate { get; set; }

		/// <summary>
		/// Has the user started watching, is it planned?
		/// </summary>
		public WatchStatus Status { get; set; }

		/// <summary>
		/// The ID of the episode started.
		/// </summary>
		[SerializeIgnore] public Guid NextEpisodeId { get; set; }

		/// <summary>
		/// The <see cref="Show"/> started.
		/// </summary>
		public Episode? NextEpisode { get; set; }

		/// <summary>
		/// Where the player has stopped watching the episode (in seconds).
		/// </summary>
		/// <remarks>
		/// Null if the status is not Watching or if the next episode is not started.
		/// </remarks>
		[Projectable(UseMemberBody = nameof(_WatchedTime), NullConditionalRewriteSupport = NullConditionalRewriteSupport.Ignore)]
		public int? WatchedTime { get; set; }

		private int? _WatchedTime => NextEpisode?.Watched.FirstOrDefault()?.WatchedTime;
	}
}
