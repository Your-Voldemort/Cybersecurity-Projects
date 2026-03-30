// ===================
// © AngelaMos | 2026
// index.ts
// ===================

import { useMutation, useQuery } from '@tanstack/react-query'
import type { AxiosError } from 'axios'
import { API_ENDPOINTS, QUERY_KEYS, UPLOAD_TIMEOUT_MS } from '@/config'
import { apiClient } from '@/core/api'
import { transformAxiosError } from '@/core/api/errors'
import { AnalysisResponseSchema, UploadResponseSchema } from '../schemas'
import type { ApiErrorBody, UploadResponse } from '../types'

export function useUpload() {
  return useMutation<
    UploadResponse,
    ReturnType<typeof transformAxiosError>,
    File
  >({
    mutationFn: async (file: File) => {
      const form = new FormData()
      form.append('file', file)

      const { data } = await apiClient.post(API_ENDPOINTS.UPLOAD, form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: UPLOAD_TIMEOUT_MS,
      })

      return UploadResponseSchema.parse(data)
    },
    onError: (error) => {
      return transformAxiosError(error as unknown as AxiosError<ApiErrorBody>)
    },
  })
}

export function useAnalysis(slug: string) {
  return useQuery({
    queryKey: QUERY_KEYS.ANALYSIS.BY_SLUG(slug),
    queryFn: async () => {
      const { data } = await apiClient.get(API_ENDPOINTS.ANALYSIS(slug))
      return AnalysisResponseSchema.parse(data)
    },
    enabled: slug.length > 0,
    staleTime: Infinity,
    refetchOnWindowFocus: false,
  })
}
