import type { QueryKey, UseMutationOptions, UseMutationResult, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';
import type { ErrorResponse, ExampleArticle, HealthStatus, HistoryItem, ListHistoryParams, PredictInput, PredictionResult, Stats, SuccessResponse } from './api.schemas';
import { customFetch } from '../custom-fetch';
import type { ErrorType, BodyType } from '../custom-fetch';
type AwaitedInput<T> = PromiseLike<T> | T;
type Awaited<O> = O extends AwaitedInput<infer T> ? T : never;
type SecondParameter<T extends (...args: never) => unknown> = Parameters<T>[1];
export declare const getHealthCheckUrl: () => string;
/**
 * Returns server health status
 * @summary Health check
 */
export declare const healthCheck: (options?: RequestInit) => Promise<HealthStatus>;
export declare const getHealthCheckQueryKey: () => readonly ["/api/healthz"];
export declare const getHealthCheckQueryOptions: <TData = Awaited<ReturnType<typeof healthCheck>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof healthCheck>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof healthCheck>>, TError, TData> & {
    queryKey: QueryKey;
};
export type HealthCheckQueryResult = NonNullable<Awaited<ReturnType<typeof healthCheck>>>;
export type HealthCheckQueryError = ErrorType<unknown>;
/**
 * @summary Health check
 */
export declare function useHealthCheck<TData = Awaited<ReturnType<typeof healthCheck>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof healthCheck>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getPredictNewsUrl: () => string;
/**
 * @summary Predict if news is fake or real
 */
export declare const predictNews: (predictInput: PredictInput, options?: RequestInit) => Promise<PredictionResult>;
export declare const getPredictNewsMutationOptions: <TError = ErrorType<ErrorResponse>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof predictNews>>, TError, {
        data: BodyType<PredictInput>;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationOptions<Awaited<ReturnType<typeof predictNews>>, TError, {
    data: BodyType<PredictInput>;
}, TContext>;
export type PredictNewsMutationResult = NonNullable<Awaited<ReturnType<typeof predictNews>>>;
export type PredictNewsMutationBody = BodyType<PredictInput>;
export type PredictNewsMutationError = ErrorType<ErrorResponse>;
/**
* @summary Predict if news is fake or real
*/
export declare const usePredictNews: <TError = ErrorType<ErrorResponse>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof predictNews>>, TError, {
        data: BodyType<PredictInput>;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationResult<Awaited<ReturnType<typeof predictNews>>, TError, {
    data: BodyType<PredictInput>;
}, TContext>;
export declare const getGetStatsUrl: () => string;
/**
 * @summary Get model and usage statistics
 */
export declare const getStats: (options?: RequestInit) => Promise<Stats>;
export declare const getGetStatsQueryKey: () => readonly ["/api/stats"];
export declare const getGetStatsQueryOptions: <TData = Awaited<ReturnType<typeof getStats>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getStats>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof getStats>>, TError, TData> & {
    queryKey: QueryKey;
};
export type GetStatsQueryResult = NonNullable<Awaited<ReturnType<typeof getStats>>>;
export type GetStatsQueryError = ErrorType<unknown>;
/**
 * @summary Get model and usage statistics
 */
export declare function useGetStats<TData = Awaited<ReturnType<typeof getStats>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getStats>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getGetExamplesUrl: () => string;
/**
 * @summary Get example articles for testing
 */
export declare const getExamples: (options?: RequestInit) => Promise<ExampleArticle[]>;
export declare const getGetExamplesQueryKey: () => readonly ["/api/examples"];
export declare const getGetExamplesQueryOptions: <TData = Awaited<ReturnType<typeof getExamples>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getExamples>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof getExamples>>, TError, TData> & {
    queryKey: QueryKey;
};
export type GetExamplesQueryResult = NonNullable<Awaited<ReturnType<typeof getExamples>>>;
export type GetExamplesQueryError = ErrorType<unknown>;
/**
 * @summary Get example articles for testing
 */
export declare function useGetExamples<TData = Awaited<ReturnType<typeof getExamples>>, TError = ErrorType<unknown>>(options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof getExamples>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getListHistoryUrl: (params?: ListHistoryParams) => string;
/**
 * @summary List recent prediction history
 */
export declare const listHistory: (params?: ListHistoryParams, options?: RequestInit) => Promise<HistoryItem[]>;
export declare const getListHistoryQueryKey: (params?: ListHistoryParams) => readonly ["/api/history", ...ListHistoryParams[]];
export declare const getListHistoryQueryOptions: <TData = Awaited<ReturnType<typeof listHistory>>, TError = ErrorType<unknown>>(params?: ListHistoryParams, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof listHistory>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}) => UseQueryOptions<Awaited<ReturnType<typeof listHistory>>, TError, TData> & {
    queryKey: QueryKey;
};
export type ListHistoryQueryResult = NonNullable<Awaited<ReturnType<typeof listHistory>>>;
export type ListHistoryQueryError = ErrorType<unknown>;
/**
 * @summary List recent prediction history
 */
export declare function useListHistory<TData = Awaited<ReturnType<typeof listHistory>>, TError = ErrorType<unknown>>(params?: ListHistoryParams, options?: {
    query?: UseQueryOptions<Awaited<ReturnType<typeof listHistory>>, TError, TData>;
    request?: SecondParameter<typeof customFetch>;
}): UseQueryResult<TData, TError> & {
    queryKey: QueryKey;
};
export declare const getDeleteHistoryUrl: (id: number) => string;
/**
 * @summary Delete a history item
 */
export declare const deleteHistory: (id: number, options?: RequestInit) => Promise<SuccessResponse>;
export declare const getDeleteHistoryMutationOptions: <TError = ErrorType<ErrorResponse>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof deleteHistory>>, TError, {
        id: number;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationOptions<Awaited<ReturnType<typeof deleteHistory>>, TError, {
    id: number;
}, TContext>;
export type DeleteHistoryMutationResult = NonNullable<Awaited<ReturnType<typeof deleteHistory>>>;
export type DeleteHistoryMutationError = ErrorType<ErrorResponse>;
/**
* @summary Delete a history item
*/
export declare const useDeleteHistory: <TError = ErrorType<ErrorResponse>, TContext = unknown>(options?: {
    mutation?: UseMutationOptions<Awaited<ReturnType<typeof deleteHistory>>, TError, {
        id: number;
    }, TContext>;
    request?: SecondParameter<typeof customFetch>;
}) => UseMutationResult<Awaited<ReturnType<typeof deleteHistory>>, TError, {
    id: number;
}, TContext>;
export {};
//# sourceMappingURL=api.d.ts.map