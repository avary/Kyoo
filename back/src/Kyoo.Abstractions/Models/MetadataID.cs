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

namespace Kyoo.Abstractions.Models;

/// <summary>
/// ID and link of an item on an external provider.
/// </summary>
public class MetadataId
{
	/// <summary>
	/// The ID of the resource on the external provider.
	/// </summary>
	public string DataId { get; set; }

	/// <summary>
	/// The URL of the resource on the external provider.
	/// </summary>
	public string? Link { get; set; }
}

/// <summary>
/// ID informations about an episode.
/// </summary>
public class EpisodeId
{
	/// <summary>
	/// The Id of the show on the metadata database.
	/// </summary>
	public string ShowId { get; set; }

	/// <summary>
	/// The season number or null if absolute numbering is used in this database.
	/// </summary>
	public int? Season { get; set; }

	/// <summary>
	/// The episode number or absolute number if Season is null.
	/// </summary>
	public int Episode { get; set; }

	/// <summary>
	/// The URL of the resource on the external provider.
	/// </summary>
	public string? Link { get; set; }
}
