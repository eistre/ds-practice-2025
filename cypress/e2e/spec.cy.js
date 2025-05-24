describe('Single non-fraudulent order', () => {
  it('Create a non-fraudulent order', () => {

    // Visit the checkout page
    cy.visit('/')

    cy.get('h1').contains('Checkout Page').should('be.visible')

    // Fill in the checkout form
    cy.get('#name').clear().type('Jack Sparrow')
    cy.get('#contact').clear().type('jack.sparrow@email.com')

    // Submit the order
    cy.get('[type="submit"]').click()

    // Check if the order confirmation is displayed
    cy.contains('Order status: Order Approved', { timeout: 10000 }).should('be.visible')
  })
})

describe('Checkout Page E2E', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.get('h1').contains('Checkout Page').should('be.visible')
  })

  it('has the correct default form state and items', () => {
    cy.get('#name').should('have.value', 'John Doe')
    cy.get('#contact').should('have.value', 'john.doe@example.com')
    cy.get('#creditCard').should('have.value', '4111111111111111')
    cy.get('#expirationDate').should('have.value', '12/25')
    cy.get('#cvv').should('have.value', '123')
    cy.get('#userComment').should('contain.value', 'Please handle with care.')
    cy.get('#shippingMethod').should('have.value', 'Standard')
    cy.get('#giftWrapping').should('be.checked')
    cy.get('#terms').should('be.checked')

    cy.get('#itemList li')
      .should('have.length', 2)
      .first().should('contain.text', 'Book A - Quantity: 1')
      .next().should('contain.text', 'Book B - Quantity: 2')
  })

  context('when the backend approves the order', () => {
    it('submits and shows a random list of suggested books', () => {
      cy.intercept('POST', '**/checkout', (req) => {
        // simulate 1–5 random suggestions
        const count = Math.floor(Math.random() * 5) + 1
        const suggestedBooks = Array.from({ length: count }, (_, i) => ({
          title: `Random Title ${i + 1}`,
          author: `Author ${i + 1}`
        }))

        req.reply({
          statusCode: 200,
          body: {
            status: 'Order Approved',
            orderId: 'ORDER-' + Date.now(),
            suggestedBooks
          }
        })
      }).as('checkoutSuccess')

      // toggle a couple of inputs and assert the payload
      cy.get('#shippingMethod').select('Express').should('have.value', 'Express')
      cy.get('#giftWrapping').uncheck().should('not.be.checked')
      cy.get('[type="submit"]').click()
    
      cy.wait('@checkoutSuccess')
      .its('request.body')
      .should((body) => {
        expect(body.shippingMethod).to.equal('Express')
        expect(body.giftWrapping).to.be.false
      })

      cy.get('#response').should('be.visible')

      // verify that at least one suggestion shows and each matches "X by Y"
      cy.get('#response ul.list-disc li')
        .should('have.length.at.least', 1)
        .each(($li) => {
          cy.wrap($li).invoke('text').should('match', /.+ by .+/)
        })
    })
  })

  context('when the backend flags the order as fraudulent', () => {
    it('displays a rejection and no suggestions', () => {
      cy.intercept('POST', '**/checkout', {
        statusCode: 200,
        body: {
          status: 'Order Rejected',
          orderId: 'FRAUD-001'
        }
      }).as('checkoutFraud')

      cy.get('[type="submit"]').click()
      cy.wait('@checkoutFraud')

      cy.get('#response')
        .should('be.visible')
        .within(() => {
          cy.contains('Order status: Order Rejected')
          cy.contains('Order ID: FRAUD-001')
          cy.get('ul.list-disc').should('not.exist')
        })
    })
  })
})
