import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

function AegirNavbar() {
  return (
    <Navbar bg="dark" variant="dark" expand="lg" fixed="top">
      <Navbar.Brand href="#home">
        <img
          src="img/odin.png"
          width="30"
          height="30"
          className="d-inline-block align-top"
          alt="ODIN logo"
        />{' '}
        AEGIR
      </Navbar.Brand>
      <Navbar.Toggle aria-controls="basic-navbar-nav" />
      <Navbar.Collapse id="basic-navbar-nav">
        <Nav className="me-auto">
          <Nav.Link href="#home">Home</Nav.Link>
          <Nav.Link href="#charts">Charts</Nav.Link>
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
}

export default AegirNavbar;