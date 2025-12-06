export type GenerateResponse = {
  xml: string;
  filename: string;
};

const normalizedApiUrl = (): string => {
  const base = import.meta.env.VITE_API_URL;
  if (!base) {
    throw new Error("VITE_API_URL is not set. Add it in .env.local (e.g., https://your-backend.onrender.com).");
  }
  return base.replace(/\/$/, "");
};

export async function generateSchema(file: File): Promise<GenerateResponse> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${normalizedApiUrl()}/generate`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Request failed");
  }

  return response.json();
}

