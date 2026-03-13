import { ApiError } from "./client";

export type LlmFeature = "summary" | "rag";

function isAiAvailabilityError(error: ApiError): boolean {
  return error.category !== undefined || error.service !== undefined;
}

export function getFeatureAvailabilityMessage(feature: LlmFeature): string {
  if (feature === "rag") {
    return "RAG combina el dataset con documentos indexados. Requiere credenciales válidas y disponibilidad de embeddings.";
  }
  return "La funcionalidad LLM genera un resumen ejecutivo con el proveedor configurado. Si el servicio no está disponible, la aplicación mostrará un estado controlado.";
}

export function getFeatureErrorMessage(feature: LlmFeature, error: unknown): string {
  if (!(error instanceof ApiError) || !isAiAvailabilityError(error)) {
    return error instanceof Error ? error.message : "No fue posible completar la operación en este momento.";
  }

  if (feature === "summary") {
    if (error.code === "api_key_missing" || error.code === "api_key_invalid") {
      return "La funcionalidad LLM no está disponible actualmente por configuración del proveedor.";
    }
    if (error.code === "insufficient_quota") {
      return "La funcionalidad LLM no está disponible actualmente por configuración o cuota del proveedor.";
    }
    if (error.retryable) {
      return "La funcionalidad LLM no está disponible temporalmente. Intenta nuevamente en unos minutos.";
    }
    return "No fue posible generar el resumen en este momento.";
  }

  if (error.service === "embeddings") {
    return "RAG requiere credenciales válidas y disponibilidad de embeddings.";
  }
  if (error.code === "insufficient_quota") {
    return "RAG no está disponible actualmente por configuración, cuota o disponibilidad del proveedor.";
  }
  if (error.retryable) {
    return "RAG no está disponible temporalmente por el proveedor. Intenta nuevamente en unos minutos.";
  }
  return "No fue posible responder la consulta con contexto documental en este momento.";
}
