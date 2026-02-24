// should work for our testing purposes with gitlab-ci
// set timezone to amsterdam for date testing
module.exports = async () => {
  process.env["TZ"] = 'Europe/Amsterdam';
};
