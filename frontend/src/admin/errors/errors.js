export default {
  ExpireTokenException: (message) => {
    this.message = message
    this.name = 'ExpireTokenException'
  },
  TimeoutException: (message) => {
    this.message = message
    this.name = 'TimeoutException'
  }
}
