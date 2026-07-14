import { Link } from "react-router-dom";

function Page2() {
  return (
    <>
      <h1>Page2</h1>

      <Link to="/">Page1へ</Link>
      <br />
      <Link to="/page3">Page3へ</Link>
    </>
  );
}

export default Page2;