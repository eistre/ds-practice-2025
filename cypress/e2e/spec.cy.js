describe('Single non-fraudulent order', () => {
  it('Create a non-fraudulent order', () => {

    // Visit the checkout page
    cy.visit('http://localhost:8080')

    // Check if the checkout page is loaded
    cy.contains('Checkout Page').should('be.visible')

    // Fill in the checkout form
    cy.get('#name').clear().type('Jack Sparrow')
    cy.get('#contact').clear().type('jack.sparrow@email.com')

    // Submit the order
    cy.get('[type="submit"]').click()

    // Check if the order confirmation is displayed
    cy.contains('Order status: Order Approved', { timeout: 10000 }).should('be.visible')
  })
})
