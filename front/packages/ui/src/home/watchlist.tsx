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

import {
	type QueryIdentifier,
	type Watchlist,
	WatchlistP,
	getDisplayDate,
	useAccount,
} from "@kyoo/models";
import { Button, P, ts } from "@kyoo/primitives";
import { useTranslation } from "react-i18next";
import { View } from "react-native";
import { useYoshiki } from "yoshiki/native";
import { ItemGrid } from "../browse/grid";
import { EpisodeBox, episodeDisplayNumber } from "../details/episode";
import { InfiniteFetch } from "../fetch-infinite";
import { Header } from "./genre";

export const WatchlistList = () => {
	const { t } = useTranslation();
	const { css } = useYoshiki();
	const account = useAccount();

	return (
		<>
			<Header title={t("home.watchlist")} />
			{account ? (
				<InfiniteFetch
					query={WatchlistList.query()}
					layout={{ ...ItemGrid.layout, layout: "horizontal" }}
					getItemType={(x, i) =>
						(x.kind === "show" && x.watchStatus?.nextEpisode) || (x.isLoading && i % 2)
							? "episode"
							: "item"
					}
					getItemSize={(kind) => (kind === "episode" ? 2 : 1)}
					empty={t("home.none")}
				>
					{(x, i) => {
						const episode = x.kind === "show" ? x.watchStatus?.nextEpisode : null;
						return (x.kind === "show" && x.watchStatus?.nextEpisode) || (x.isLoading && i % 2) ? (
							<EpisodeBox
								isLoading={x.isLoading as any}
								slug={episode?.slug}
								showSlug={x.slug}
								name={episode ? `${x.name} ${episodeDisplayNumber(episode)}` : undefined}
								overview={episode?.name}
								thumbnail={episode?.thumbnail ?? x.thumbnail}
								href={episode?.href}
								watchedPercent={x.watchStatus?.watchedPercent || null}
								watchedStatus={x.watchStatus?.status || null}
								// TODO: Move this into the ItemList (using getItemSize)
								// @ts-expect-error This is a web only property
								{...css({ gridColumnEnd: "span 2" })}
							/>
						) : (
							<ItemGrid
								isLoading={x.isLoading as any}
								href={x.href}
								slug={x.slug}
								name={x.name!}
								subtitle={!x.isLoading ? getDisplayDate(x) : undefined}
								poster={x.poster}
								watchStatus={x.watchStatus?.status || null}
								watchPercent={x.watchStatus?.watchedPercent || null}
								unseenEpisodesCount={x.kind === "show" ? x.watchStatus?.unseenEpisodesCount : null}
								type={x.kind}
							/>
						);
					}}
				</InfiniteFetch>
			) : (
				<View {...css({ justifyContent: "center", alignItems: "center" })}>
					<P>{t("home.watchlistLogin")}</P>
					<Button
						text={t("login.login")}
						href={"/login"}
						{...css({ minWidth: ts(24), margin: ts(2) })}
					/>
				</View>
			)}
		</>
	);
};

WatchlistList.query = (): QueryIdentifier<Watchlist> => ({
	parser: WatchlistP,
	infinite: true,
	path: ["watchlist"],
	params: {
		// Limit the inital numbers of items
		limit: 10,
		fields: ["watchStatus"],
	},
});
