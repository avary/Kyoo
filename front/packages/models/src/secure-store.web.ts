/*
 * Kyoo - A portable and vast media library solution.
 * Copyright (c) Kyoo.
 *
 * See AUTHORS.md and LICENSE file in the project root for full license information.
 *
 * Kyoo is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * any later version.
 *
 * Kyoo is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Kyoo. If not, see <https://www.gnu.org/licenses/>.
 */

export const setSecureItemSync = (key: string, value: string | null) => {
	const d = new Date();
	// A year
	d.setTime(d.getTime() + 365 * 24 * 60 * 60 * 1000);
	const expires = value ? "expires=" + d.toUTCString() : "expires=Thu, 01 Jan 1970 00:00:01 GMT";
	document.cookie = key + "=" + value + ";" + expires + ";path=/";
	return null;
};

export const setSecureItem = async (key: string, value: string | null): Promise<null> =>
	setSecureItemSync(key, value);

export const deleteSecureItem = async (key: string) => setSecureItem(key, null);

export const getSecureItem = async (key: string, cookies?: string): Promise<string | null> => {
	// Don't try to use document's cookies on SSR.
	if (!cookies && typeof window === "undefined") return null;
	const name = key + "=";
	const decodedCookie = decodeURIComponent(cookies ?? document.cookie);
	const ca = decodedCookie.split(";");
	for (let i = 0; i < ca.length; i++) {
		let c = ca[i];
		while (c.charAt(0) == " ") {
			c = c.substring(1);
		}
		if (c.indexOf(name) == 0) {
			return c.substring(name.length, c.length);
		}
	}
	return null;
};