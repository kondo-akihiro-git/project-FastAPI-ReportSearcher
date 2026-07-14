import { Link } from "react-router-dom";

function Page1() {
  return (
    <>
      <h1>Page1</h1>

      <Link to="/page2">Page2へ</Link>
      <br />
      <Link to="/page3">Page3へ</Link>
    </>
  );
}

export default Page1;