import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import ContactPage from '../pages/ContactPage'

vi.mock('../api/contact', () => ({
  sendMessage: vi.fn(),
}))

import { sendMessage } from '../api/contact'

function renderContact() {
  return render(<MemoryRouter><ContactPage /></MemoryRouter>)
}

beforeEach(() => {
  vi.clearAllMocks()
})

describe('ContactPage — rendering', () => {
  it('renders heading', () => {
    renderContact()
    expect(screen.getByRole('heading', { name: /kontakt/i })).toBeInTheDocument()
  })

  it('renders all form fields', () => {
    renderContact()
    expect(screen.getByLabelText(/imię i nazwisko/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/temat/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/wiadomość/i)).toBeInTheDocument()
  })

  it('renders submit button', () => {
    renderContact()
    expect(screen.getByRole('button', { name: /wyślij wiadomość/i })).toBeInTheDocument()
  })
})

describe('ContactPage — form submission', () => {
  async function fillAndSubmit() {
    await userEvent.type(screen.getByLabelText(/imię i nazwisko/i), 'Jan Kowalski')
    await userEvent.type(screen.getByLabelText(/email/i), 'jan@test.pl')
    await userEvent.type(screen.getByLabelText(/temat/i), 'Zapytanie')
    await userEvent.type(screen.getByLabelText(/wiadomość/i), 'Treść wiadomości testowej.')
    await userEvent.click(screen.getByRole('button', { name: /wyślij wiadomość/i }))
  }

  it('calls sendMessage with form data', async () => {
    sendMessage.mockResolvedValue({ data: {} })
    renderContact()
    await fillAndSubmit()
    await waitFor(() => {
      expect(sendMessage).toHaveBeenCalledWith(
        expect.objectContaining({
          name: 'Jan Kowalski',
          email: 'jan@test.pl',
          subject: 'Zapytanie',
          message: 'Treść wiadomości testowej.',
        })
      )
    })
  })

  it('shows success state after sending', async () => {
    sendMessage.mockResolvedValue({ data: {} })
    renderContact()
    await fillAndSubmit()
    await waitFor(() => {
      expect(screen.getByText(/wiadomość wysłana/i)).toBeInTheDocument()
    })
  })

  it('hides form after success', async () => {
    sendMessage.mockResolvedValue({ data: {} })
    renderContact()
    await fillAndSubmit()
    await waitFor(() => {
      expect(screen.queryByRole('button', { name: /wyślij/i })).not.toBeInTheDocument()
    })
  })

  it('shows field error from API', async () => {
    sendMessage.mockRejectedValue({ response: { data: { email: ['Podaj prawidłowy adres email.'] } } })
    renderContact()
    await fillAndSubmit()
    await waitFor(() => {
      expect(screen.getByText(/podaj prawidłowy adres email/i)).toBeInTheDocument()
    })
  })

  it('disables button while sending', async () => {
    sendMessage.mockReturnValue(new Promise(() => {}))
    renderContact()
    await userEvent.type(screen.getByLabelText(/imię i nazwisko/i), 'Jan')
    await userEvent.type(screen.getByLabelText(/email/i), 'j@j.pl')
    await userEvent.type(screen.getByLabelText(/temat/i), 'T')
    await userEvent.type(screen.getByLabelText(/wiadomość/i), 'M')
    await userEvent.click(screen.getByRole('button', { name: /wyślij wiadomość/i }))
    expect(screen.getByRole('button', { name: /wysyłanie/i })).toBeDisabled()
  })
})
