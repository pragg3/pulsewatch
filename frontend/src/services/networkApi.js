const API_URL = '/api'

async function readResponse(response) {
  const contentType = response.headers.get('content-type') || ''

  if (!contentType.includes('application/json')) {
    throw new Error(
      'API returned an unexpected response. Check the API proxy.',
    )
  }

  let data

  try {
    data = await response.json()
  } catch {
    throw new Error('API returned invalid JSON.')
  }

  if (!response.ok) {
    const error = new Error(
      data?.detail || 'Network request failed',
    )

    error.status = response.status
    throw error
  }

  return data
}

export async function getNetworkInfo(discoveryKey) {
  const response = await fetch(`${API_URL}/network/info`, {
    headers: {
      'X-PulseWatch-Discovery-Key': discoveryKey,
    },
  })

  return readResponse(response)
}

export async function discoverNetwork(
  discoveryKey,
  startIp,
  endIp,
) {
  const response = await fetch(
    `${API_URL}/network/discover`,
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-PulseWatch-Discovery-Key': discoveryKey,
      },
      body: JSON.stringify({
        start_ip: startIp,
        end_ip: endIp,
      }),
    },
  )

  return readResponse(response)
}