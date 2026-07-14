
import { Link } from "react-router-dom";

function Page3() {
  return (
    <>
      <h1>Page3</h1>

      <Link to="/">Page1へ</Link>
      <br />
      <Link to="/page2">Page2へ</Link>
    </>
  );
}

export default Page3;