const boilerplate = {
  python: `
def main() -> None:
    print("Hello world !")
    
if __name__ == "__main__":
    main()
`,

  rust: `
fn main() {
    println!("Hello World!");
}
`,
};

export default boilerplate;
