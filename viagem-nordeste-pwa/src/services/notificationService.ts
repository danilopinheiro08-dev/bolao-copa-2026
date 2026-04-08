/**
 * Notification Service — Viagem Nordeste PWA
 *
 * Camadas de notificação:
 * 1. BroadcastChannel — sincronização entre abas do mesmo navegador (mesmo celular)
 * 2. Web Notification API — popup nativo do navegador (funciona mesmo com app minimizado)
 * 3. ntfy.sh — push notification gratuito entre dispositivos diferentes
 *    → Usuários devem instalar o app ntfy.sh (Android/iOS) e assinar o tópico
 *    → Tópico configurável abaixo
 */

// ── Configuração ─────────────────────────────────────────────────────────────
// Altere o tópico para algo único do seu grupo (evita colisão com outros usuários)
export const NTFY_TOPIC = 'viagem-nordeste-abril-2026-grupo'
const NTFY_BASE_URL = 'https://ntfy.sh'

// Canal BroadcastChannel para sync entre abas
const BROADCAST_CHANNEL_NAME = 'viagem-nordeste'
let channel: BroadcastChannel | null = null

function getChannel(): BroadcastChannel | null {
  if (typeof BroadcastChannel === 'undefined') return null
  if (!channel) channel = new BroadcastChannel(BROADCAST_CHANNEL_NAME)
  return channel
}

// ── 1. BroadcastChannel ───────────────────────────────────────────────────────

export interface BroadcastPayload {
  type: 'new-event' | 'remove-event'
  title: string
  travelerName: string
  date: string
  time: string
}

export function broadcastToTabs(payload: BroadcastPayload) {
  getChannel()?.postMessage(payload)
}

export function listenBroadcast(callback: (p: BroadcastPayload) => void): () => void {
  const ch = getChannel()
  if (!ch) return () => {}
  const handler = (e: MessageEvent) => callback(e.data as BroadcastPayload)
  ch.addEventListener('message', handler)
  return () => ch.removeEventListener('message', handler)
}

// ── 2. Web Notification API ──────────────────────────────────────────────────

export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!('Notification' in window)) return 'denied'
  if (Notification.permission === 'granted') return 'granted'
  return Notification.requestPermission()
}

export function showBrowserNotification(title: string, body: string, icon = '/icons/icon-192.png') {
  if (!('Notification' in window) || Notification.permission !== 'granted') return
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    new (window.Notification as any)(title, {
      body,
      icon,
      badge: icon,
      vibrate: [200, 100, 200],
      tag: 'viagem-nordeste',
      renotify: true,
    })
  } catch { /* ServiceWorker pode estar bloqueando em alguns browsers */ }
}

// ── 3. ntfy.sh — Push Cross-Device ──────────────────────────────────────────

/**
 * Envia notificação push para TODOS os dispositivos inscritos no tópico.
 *
 * Para receber no celular:
 *   Android/iOS: instale o app "ntfy" → assine o tópico: viagem-nordeste-abril-2026-grupo
 *   Web: acesse https://ntfy.sh/viagem-nordeste-abril-2026-grupo e clique em "Subscribe"
 */
export async function pushToGroup(
  title: string,
  message: string,
  emoji = '📅',
): Promise<boolean> {
  try {
    const res = await fetch(`${NTFY_BASE_URL}/${NTFY_TOPIC}`, {
      method: 'POST',
      headers: {
        'Title': `${emoji} ${title}`,
        'Priority': 'default',
        'Tags': 'calendar,beach,palm_tree',
        'Content-Type': 'text/plain; charset=utf-8',
      },
      body: message,
    })
    return res.ok
  } catch {
    return false
  }
}

// ── Helper principal ─────────────────────────────────────────────────────────

/**
 * Dispara todos os canais de notificação em paralelo.
 */
export async function notifyAll(params: {
  title: string
  message: string
  travelerName: string
  date: string
  time: string
}) {
  const { title, message, travelerName, date, time } = params

  // BroadcastChannel (mesmo navegador)
  broadcastToTabs({ type: 'new-event', title, travelerName, date, time })

  // Web Notification (mesma aba minimizada)
  showBrowserNotification(`Roteiro atualizado!`, message)

  // ntfy.sh (outros celulares do grupo)
  await pushToGroup('Roteiro atualizado!', message, '📍')
}
