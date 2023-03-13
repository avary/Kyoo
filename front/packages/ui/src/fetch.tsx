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

import { Page, QueryIdentifier, useFetch, KyooErrors } from "@kyoo/models";
import { Breakpoint, P } from "@kyoo/primitives";
import { View } from "react-native";
import { useYoshiki } from "yoshiki/native";

export type Layout = { numColumns: Breakpoint<number>; size: Breakpoint<number> };

export type WithLoading<Item> =
	| (Item & { isLoading: false })
	| (Partial<Item> & { isLoading: true });

// We keep a Partial<Item> on the error value to allow destructuring.
export type WithError<Item> =
	| (Item & { isError: false; error: undefined })
	| (Partial<Item> & { isError: true; error: KyooErrors });

const isPage = <T = unknown,>(obj: unknown): obj is Page<T> =>
	(typeof obj === "object" && obj && "items" in obj) || false;

export const FetchNE = <Data,>({
	query,
	placeholderCount = 1,
	children,
}: {
	query: QueryIdentifier<Data>;
	placeholderCount?: number;
	children: (
		item: Data extends Page<infer Item>
			? WithError<WithLoading<Item>>
			: WithError<WithLoading<Data>>,
		i: number,
	) => JSX.Element | null;
}): JSX.Element | null => {
	const { data, error } = useFetch(query);

	// @ts-ignore
	if (error) return children({ isError: true, error }, 0);
	if (!data) {
		const placeholders = [...Array(placeholderCount)].map((_, i) =>
			children({ isLoading: true } as any, i),
		);
		return <>{placeholderCount === 1 ? placeholders[0] : placeholders}</>;
	}
	if (!isPage<object>(data))
		return children(data ? { ...data, isLoading: false } : ({ isLoading: true } as any), 0);
	return <>{data.items.map((item, i) => children({ ...item, isLoading: false } as any, i))}</>;
};

export const Fetch = <Data,>({
	children,
	...params
}: {
	query: QueryIdentifier<Data>;
	placeholderCount?: number;
	children: (
		item: Data extends Page<infer Item> ? WithLoading<Item> : WithLoading<Data>,
		i: number,
	) => JSX.Element | null;
}): JSX.Element | null => {
	return (
		<FetchNE {...params}>
			{({ isError, error, ...item }, i) =>
				// @ts-ignore
				isError ? <ErrorView error={error} /> : children(item, i)
			}
		</FetchNE>
	);
};

export const ErrorView = ({ error }: { error: KyooErrors }) => {
	const { css } = useYoshiki();

	return (
		<View
			{...css({
				backgroundColor: (theme) => theme.colors.red,
				flexGrow: 1,
				flexShrink: 1,
				justifyContent: "center",
				alignItems: "center",
			})}
		>
			{error.errors.map((x, i) => (
				<P key={i} {...css({ color: (theme) => theme.colors.white })}>
					{x}
				</P>
			))}
		</View>
	);
};

export const EmptyView = ({ message }: { message: string }) => {
	const { css } = useYoshiki();

	return (
		<View
			{...css({
				flexGrow: 1,
				flexShrink: 1,
				justifyContent: "center",
				alignItems: "center",
			})}
		>
			<P {...css({ color: (theme) => theme.heading })}>{message}</P>
		</View>
	);
};